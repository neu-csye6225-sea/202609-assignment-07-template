# Assignment 7 infrastructure (provided). See README.md, "Appendix A: Infrastructure Reference".
# You should not need to change this file: later assignments build on these resources.

# ---------------------------------------------------------------- AMI
# Ubuntu 22.04 LTS (amd64) published by Canonical. Ubuntu 22.04 only publishes ebs-gp2 paths.
data "aws_ssm_parameter" "ubuntu_2204" {
  name = "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id"
}

# ---------------------------------------------------------------- network
resource "aws_vpc" "main" {
  cidr_block           = "10.70.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "a7-vpc" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.70.1.0/24"
  availability_zone       = "us-west-2a"
  map_public_ip_on_launch = true

  tags = { Name = "a7-public-subnet" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = { Name = "a7-igw" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = { Name = "a7-public-rt" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# ---------------------------------------------------------------- security group
resource "aws_security_group" "api" {
  name        = "a7-api-sg"
  description = "Library API: port 8080 from anywhere, SSH from one address"
  vpc_id      = aws_vpc.main.id

  tags = { Name = "a7-api-sg" }
}

resource "aws_vpc_security_group_ingress_rule" "api" {
  security_group_id = aws_security_group.api.id
  description       = "Library API"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 8080
  to_port           = 8080
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  count             = var.ssh_cidr == "" ? 0 : 1
  security_group_id = aws_security_group.api.id
  description       = "SSH from my IP"
  cidr_ipv4         = var.ssh_cidr
  ip_protocol       = "tcp"
  from_port         = 22
  to_port           = 22
}

resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.api.id
  description       = "All outbound"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# ---------------------------------------------------------------- instance
resource "aws_instance" "api" {
  ami                    = data.aws_ssm_parameter.ubuntu_2204.value
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.api.id]
  key_name               = var.key_name == "" ? null : var.key_name

  # Copies app/server.py onto the instance and runs it as a systemd service.
  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    server_py_b64gz = base64gzip(file("${path.module}/../app/server.py"))
  })
  user_data_replace_on_change = true # a change to server.py replaces the instance

  metadata_options {
    http_tokens = "required"
  }

  tags = { Name = "a7-library-api" }
}
