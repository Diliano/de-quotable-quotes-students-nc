terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "quotable-quotes-state-bucket"
    key    = "de-quote-pipe/terraform.tfstate"
    region = "eu-west-2"
  }
}

provider "aws" {
  region = "eu-west-2"
  default_tags {
    tags = {
      ProjectName   = "Quote Pipe"
      Team          = "Data Engineering"
      DeployedFrom  = "Terraform"
      Repository    = "de-quote-pipe"
      CostCentre    = "DE"
      Environment   = "dev"
      RetentionDate = "2024-05-31"
    }
  }
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}
