terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.0.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# 1. IAM Execution Role for Lambda Functions
resource "aws_iam_role" "lambda_exec" {
  name = "${var.app_name}-lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach basic execution policy (allows CloudWatch Logging)
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 2. Local variables mapping 15 functions
locals {
  runtimes = ["python3.11", "nodejs20.x", "java17"]
  memories = [128, 256, 512, 1024, 2048]

  # Generate combination map of: "{prefix}_{memory}"
  functions = {
    for pair in setproduct(local.runtimes, local.memories) :
    "${pair[0] == "python3.11" ? "py" : pair[0] == "nodejs20.x" ? "node" : "java"}_${pair[1]}" => {
      runtime     = pair[0]
      memory      = pair[1]
      runtime_key = pair[0] == "python3.11" ? "python" : pair[0] == "nodejs20.x" ? "nodejs" : "java"
      handler     = pair[0] == "python3.11" ? "handler.lambda_handler" : pair[0] == "nodejs20.x" ? "index.handler" : "com.serverless.benchmark.Function::handleRequest"
      source_file = pair[0] == "java17" ? "${path.module}/../../../benchmarks/java/target/benchmark-1.0.jar" : "${path.module}/files/${pair[0] == "python3.11" ? "python" : "nodejs"}.zip"
    }
  }
}

# 3. Create the 15 Lambda functions
resource "aws_lambda_function" "benchmark_functions" {
  for_each = local.functions

  function_name    = "${var.app_name}-${each.key}"
  runtime          = each.value.runtime
  memory_size      = each.value.memory
  handler          = each.value.handler
  role             = aws_iam_role.lambda_exec.arn
  filename         = each.value.source_file
  source_code_hash = filebase64sha256(each.value.source_file)
  timeout          = 60
}

# 4. Create API Gateway (HTTP API v2)
resource "aws_apigatewayv2_api" "api" {
  name          = "${var.app_name}-api"
  protocol_type = "HTTP"
}

# 5. Create API Gateway Stage (dev)
resource "aws_apigatewayv2_stage" "stage" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "dev"
  auto_deploy = true
}

# 6. API Gateway Integrations for Lambda
resource "aws_apigatewayv2_integration" "lambda_integration" {
  for_each = local.functions

  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.benchmark_functions[each.key].invoke_arn
  payload_format_version = "2.0"
}

# 7. API Gateway Routes (ANY /{func_name} maps to respective Lambda integration)
resource "aws_apigatewayv2_route" "route" {
  for_each = local.functions

  api_id    = aws_apigatewayv2_api.api.id
  route_key = "ANY /${each.key}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration[each.key].id}"
}

# 8. Lambda invocation permissions for API Gateway
resource "aws_lambda_permission" "apigw_lambda" {
  for_each = local.functions

  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.benchmark_functions[each.key].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}
