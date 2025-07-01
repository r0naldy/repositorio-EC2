output "public_ip" {
  description = "IP pública de la instancia EC2"
  value       = aws_instance.consumer_ec2.public_ip
}

output "instance_id" {
  description = "ID de la instancia EC2 creada"
  value       = aws_instance.consumer_ec2.id
}

output "rds_endpoint" {
  value = aws_db_instance.ventas.endpoint
}
