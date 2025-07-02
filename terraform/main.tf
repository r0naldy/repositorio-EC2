resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
}

resource "aws_security_group" "allow_http_mysql" {
  name        = "allow_http_mysql"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Flask ap
  }

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # MySQL
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "ventas" {
  identifier         = "data-ventas"
  allocated_storage  = 20
  engine             = "mysql"
  engine_version     = "8.0.41"
  instance_class     = "db.t3.micro"
  db_name            = "ventas"
  username           = var.db_username
  password           = var.db_password
  publicly_accessible = true
  vpc_security_group_ids = [aws_security_group.allow_http_mysql.id]
  db_subnet_group_name   = aws_db_subnet_group.default.name
  skip_final_snapshot    = true
}

resource "aws_db_subnet_group" "default" {
  name       = "main-subnet-group"
  subnet_ids = [aws_subnet.public.id]
}

resource "aws_instance" "app_server" {
  ami                    = "ami-0c2b8ca1dad447f8a"  # Amazon Linux 2
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.allow_http_mysql.id]
  associate_public_ip_address = true
  key_name               = "your-key-name"

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install python3 -y
              pip3 install flask flask_sqlalchemy mysql-connector-python
              mkdir -p /app
              cd /app
              git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .
              nohup python3 app/app.py > /dev/null 2>&1 &
              EOF

  tags = {
    Name = "FlaskAppServer"
  }
}
