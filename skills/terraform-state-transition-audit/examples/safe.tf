moved {
  from = aws_instance.old
  to = aws_instance.new
}
moved {
  from = module.old
  to = module.new
}
removed {
  from = aws_s3_bucket.retired
  lifecycle {
    destroy = false
  }
}
