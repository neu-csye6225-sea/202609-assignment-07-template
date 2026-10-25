# The autograder reads api_base_url from the committed terraform.tfstate.
output "api_base_url" {
  description = "Base URL of the Library API"
  value       = "http://${aws_instance.api.public_ip}:8080"
}

output "instance_public_ip" {
  value = aws_instance.api.public_ip
}

output "instance_id" {
  value = aws_instance.api.id
}
