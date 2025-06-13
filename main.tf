terraform {
  backend "s3" {
    bucket = "bdlab-juice-shop-tfstate"   # <-- your bucket name here
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "juice_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "juice_subnet" {
  vpc_id                  = aws_vpc.juice_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"  # Explicitly set the availability zone
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.juice_vpc.id
}

resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.juice_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table_association" "rta" {
  subnet_id      = aws_subnet.juice_subnet.id
  route_table_id = aws_route_table.rt.id
}

resource "aws_security_group" "juice_sg" {
  name        = "juice-sg"
  description = "Allow HTTP"
  vpc_id      = aws_vpc.juice_vpc.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "juice_instance" {
  ami                    = "ami-0c2b8ca1dad447f8a" # Amazon Linux 2 AMI (HVM), SSD Volume Type
  instance_type          = "t3.medium"  # Updated instance type
  subnet_id              = aws_subnet.juice_subnet.id
  vpc_security_group_ids = [aws_security_group.juice_sg.id]
  associate_public_ip_address = true
  key_name               = var.key_name

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              amazon-linux-extras install docker -y
              service docker start
              usermod -a -G docker ec2-user
              docker run -d -p 80:3000 bkimminich/juice-shop:v9.3.1
              EOF

  tags = {
    Name = "JuiceShopInstance"
  }
}
