output "function_urls" {
  value       = { for name, fn in google_cloudfunctions2_function.benchmark_functions : name => fn.service_config[0].uri }
  description = "The URLs of the deployed Cloud Functions"
}

# Automatically generate endpoints.json for the benchmark runner
resource "local_file" "endpoints_json" {
  content  = jsonencode({
    for name, fn in google_cloudfunctions2_function.benchmark_functions :
    name => fn.service_config[0].uri
  })
  filename = "${path.module}/../../../experimentation/endpoints.json"
}
