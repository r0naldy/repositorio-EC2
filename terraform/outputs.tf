output "public_ip" {
  value = aws_instance.app_server.public_ip
}

output "instance_id" {
  value = aws_instance.app_server.id
}

output "rds_endpoint" {
  value = aws_db_instance.ventas.endpoint
}
