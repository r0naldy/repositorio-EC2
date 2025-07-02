variable "region" {
  default = "us-east-1"
}

variable "instance_type" {
  default = "t2.micro"
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

