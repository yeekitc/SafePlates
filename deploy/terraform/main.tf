terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-2"
}

# EC2 Instance
resource "aws_instance" "backend_server" {
  ami             = "ami-0e83be366243f524a"
  instance_type   = "t2.micro"

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y python3 python3-pip git
              
              # Clone the main repository
              cd /home/ubuntu
              git clone ${var.repo_url} allerfree
              
              # Navigate to backend directory
              cd allerfree/backend
              
              # Install Python dependencies
              pip3 install -r requirements.txt
              
              # Install PM2 and PM2 Python support
              curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
              apt-get install -y nodejs
              npm install -g pm2
              pm2 install python

              # Set up environment variables
              echo "MONGODB_URI=${var.mongodb_uri}" >> .env
              
              # Start FastAPI with PM2 and uvicorn
              cd /home/ubuntu/allerfree/backend
              pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name "backend"
              
              # Ensure PM2 starts on reboot
              pm2 startup
              pm2 save
              EOF

  tags = {
    Name = "technica-backend"
  }
}

# Output the public IP
output "public_ip" {
  value = aws_instance.backend_server.public_ip
}