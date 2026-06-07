output "function_urls" {
  value = merge(
    { for mem in [128, 256, 512, 1024, 2048] : "py_${mem}" => "https://${azurerm_linux_function_app.python.default_hostname}/api/py_${mem}" },
    { for mem in [128, 256, 512, 1024, 2048] : "node_${mem}" => "https://${azurerm_linux_function_app.nodejs.default_hostname}/api/node_${mem}" },
    { for mem in [128, 256, 512, 1024, 2048] : "java_${mem}" => "https://${azurerm_linux_function_app.java.default_hostname}/api/java_${mem}" }
  )
  description = "The HTTP endpoints of the Azure functions"
}

resource "local_file" "endpoints_json" {
  content = jsonencode(merge(
    { for mem in [128, 256, 512, 1024, 2048] : "py_${mem}" => "https://${azurerm_linux_function_app.python.default_hostname}/api/py_${mem}" },
    { for mem in [128, 256, 512, 1024, 2048] : "node_${mem}" => "https://${azurerm_linux_function_app.nodejs.default_hostname}/api/node_${mem}" },
    { for mem in [128, 256, 512, 1024, 2048] : "java_${mem}" => "https://${azurerm_linux_function_app.java.default_hostname}/api/java_${mem}" }
  ))
  filename = "${path.module}/../../../experimentation/endpoints_azure.json"
}
