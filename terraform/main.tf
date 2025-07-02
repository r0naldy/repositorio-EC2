
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "main-vpc"
  }
}


resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-a"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-b"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "internet-gateway"
  }
}


resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "public-route-table"
  }
}

# Asociar tabla de rutas a subred pública A
resource "aws_route_table_association" "public_subnet_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

# Asociar tabla de rutas a subred pública B
resource "aws_route_table_association" "public_subnet_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

# Subnet Group para RDS
resource "aws_db_subnet_group" "default" {
  name       = "main-subnet-group-v2"
  subnet_ids = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]

  tags = {
    Name = "rds-subnet-group"
  }
}

# Seguridad para Flask y MySQL
resource "aws_security_group" "allow_http_mysql" {
  name   = "allow_http_mysql"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "flask-mysql-sg"
  }
}

# RDS MySQL
resource "aws_db_instance" "ventas" {
  identifier              = "data-ventas"
  allocated_storage       = 20
  engine                  = "mysql"
  engine_version          = "8.0.41"
  instance_class          = "db.t3.micro"
  db_name                 = "ventas"
  username                = var.db_username
  password                = var.db_password
  publicly_accessible     = true
  vpc_security_group_ids  = [aws_security_group.allow_http_mysql.id]
  db_subnet_group_name    = aws_db_subnet_group.default.name
  skip_final_snapshot     = true
}

# EC2 con Flask App
resource "aws_instance" "app_server" {
  ami                         = "ami-0c2b8ca1dad447f8a" # Amazon Linux 2
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public_a.id
  vpc_security_group_ids      = [aws_security_group.allow_http_mysql.id]
  associate_public_ip_address = true
  key_name                    = "ec2"
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install python3 -y
              pip3 install flask flask_sqlalchemy mysql-connector-python boto3
              mkdir -p /app
              cd /app
              git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .  # Cambia esto
              nohup python3 app.py > /dev/null 2>&1 &
              EOF

  tags = {
    Name = "FlaskAppServer"
  }
}

# IAM Role para EC2 con permisos S3
resource "aws_iam_role" "ec2_role" {
  name = "ec2_s3_access_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

# Política de acceso a S3
resource "aws_iam_role_policy" "s3_policy" {
  name = "ec2_s3_policy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      Resource = [
        "arn:aws:s3:::${var.bucket_name}",
        "arn:aws:s3:::${var.bucket_name}/*"
      ]
    }]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2_profile_v2"  
  role = aws_iam_role.ec2_role.name
}