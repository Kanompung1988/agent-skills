moved {
  from = aws_instance.a
  to = aws_instance.b
}
moved {
  from = aws_instance.b
  to = aws_instance.a
}
removed {
  from = aws_instance.a
  lifecycle {
    destroy = true
  }
}
