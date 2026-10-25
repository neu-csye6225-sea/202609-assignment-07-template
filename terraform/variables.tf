variable "region" {
  description = "AWS region. This assignment must be deployed in us-west-2."
  type        = string
  default     = "us-west-2"

  validation {
    condition     = var.region == "us-west-2"
    error_message = "This assignment must be deployed in us-west-2."
  }
}

variable "instance_type" {
  description = "EC2 instance type (t2.micro or t3.micro)."
  type        = string
  default     = "t3.micro"
}

variable "ssh_cidr" {
  description = "Your public IP as a /32 (for example 203.0.113.25/32) to allow SSH. Leave empty for no SSH."
  type        = string
  default     = ""
}

variable "key_name" {
  description = "Name of an existing EC2 key pair for SSH. Leave empty for none."
  type        = string
  default     = ""
}
