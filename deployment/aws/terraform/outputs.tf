output "api_endpoint" {
  value       = aws_apigatewayv2_stage.stage.invoke_url
  description = "The HTTP API Gateway URL"
}

output "function_urls" {
  value = {
    for name, fn in aws_lambda_function.benchmark_functions :
    name => "${aws_apigatewayv2_stage.stage.invoke_url}/${name}"
  }
  description = "The HTTP endpoints of the benchmark functions"
}

resource "local_file" "endpoints_json" {
  content = jsonencode({
    for name, fn in aws_lambda_function.benchmark_functions :
    name => "${aws_apigatewayv2_stage.stage.invoke_url}/${name}"
  })
  filename = "${path.module}/../../../experimentation/endpoints_aws.json"
}
