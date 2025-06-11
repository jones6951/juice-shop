output "juice_shop_url" {
  description = "Juice Shop URL"
  value       = "http://${aws_instance.juice_instance.public_ip}"
}
