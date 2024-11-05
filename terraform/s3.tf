resource "aws_s3_bucket" "testing_bucket" {
  bucket_prefix = "${var.S3_BUCKET_PREFIX}-"

  force_destroy = true
}
