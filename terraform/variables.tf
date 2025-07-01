variable "aws_region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "key_name" {
  description = "Nombre del par de claves EC2"
  type        = string
  default     = "ec2"  
}

variable "instance_type" {
  description = "Tipo de instancia EC2"
  type        = string
  default     = "t2.micro"
}

variable "bucket_name" {
  description = "Nombre del bucket S3 donde están los JSON"
  type        = string
  default     = "bucket-json-clear" 
}

variable "db_username" {
  default = "root"
}

variable "db_password" {
  default = "ventas123"
}

