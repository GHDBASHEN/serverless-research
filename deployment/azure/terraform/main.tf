terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.0.0"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.0.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Random suffix for unique resource names
resource "random_id" "suffix" {
  byte_length = 4
}

# 1. Resource Group
resource "azurerm_resource_group" "rg" {
  name     = "${var.app_name}-rg-${random_id.suffix.hex}"
  location = var.location
}

# 2. Storage Account (required by Azure Function App)
resource "azurerm_storage_account" "sa" {
  name                     = "sa${random_id.suffix.hex}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# 3. Storage Container for Code Zips
resource "azurerm_storage_container" "code" {
  name                  = "function-releases"
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "private"
}

# 4. Upload Function Zips to Storage Blob
resource "azurerm_storage_blob" "zip" {
  for_each = {
    python = "${path.module}/files/python.zip"
    nodejs = "${path.module}/files/nodejs.zip"
    java   = "${path.module}/files/java.zip"
  }

  name                   = "${each.key}-${filemd5(each.value)}.zip"
  storage_account_name   = azurerm_storage_account.sa.name
  storage_container_name = azurerm_storage_container.code.name
  type                   = "Block"
  source                 = each.value
}

# 5. Service Plan (App Service Plan)
resource "azurerm_service_plan" "plan" {
  name                = "${var.app_name}-plan-${random_id.suffix.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1" # B1 = Basic App Service Plan
}

# Generate SAS URL with read permissions for the zip packages
data "azurerm_storage_account_sas" "sas" {
  connection_string = azurerm_storage_account.sa.primary_connection_string
  https_only        = true

  resource_types {
    service   = false
    container = false
    object    = true
  }

  services {
    blob  = true
    queue = false
    table = false
    file  = false
  }

  start  = "2026-01-01T00:00:00Z"
  expiry = "2030-01-01T00:00:00Z"

  permissions {
    read    = true
    write   = false
    delete  = false
    list    = false
    add     = false
    create  = false
    update  = false
    process = false
    tag     = false
    filter  = false
  }
}

# Locals for App configuration
locals {
  sas_token = data.azurerm_storage_account_sas.sas.sas
  
  # Helper to construct SAS URL
  sas_url = {
    for k, blob in azurerm_storage_blob.zip :
    k => "https://${azurerm_storage_account.sa.name}.blob.core.windows.net/${azurerm_storage_container.code.name}/${blob.name}${local.sas_token}"
  }
}

# 6. Create the Function App for Python
resource "azurerm_linux_function_app" "python" {
  name                = "${var.app_name}-py-${random_id.suffix.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  storage_account_name       = azurerm_storage_account.sa.name
  storage_account_access_key = azurerm_storage_account.sa.primary_access_key
  service_plan_id            = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    WEBSITE_RUN_FROM_PACKAGE = local.sas_url["python"]
    FUNCTIONS_WORKER_RUNTIME = "python"
  }
}

# 7. Create the Function App for Node.js
resource "azurerm_linux_function_app" "nodejs" {
  name                = "${var.app_name}-node-${random_id.suffix.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  storage_account_name       = azurerm_storage_account.sa.name
  storage_account_access_key = azurerm_storage_account.sa.primary_access_key
  service_plan_id            = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      node_version = "20"
    }
  }

  app_settings = {
    WEBSITE_RUN_FROM_PACKAGE = local.sas_url["nodejs"]
    FUNCTIONS_WORKER_RUNTIME = "node"
  }
}

# 8. Create the Function App for Java
resource "azurerm_linux_function_app" "java" {
  name                = "${var.app_name}-java-${random_id.suffix.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  storage_account_name       = azurerm_storage_account.sa.name
  storage_account_access_key = azurerm_storage_account.sa.primary_access_key
  service_plan_id            = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      java_version = "17"
    }
  }

  app_settings = {
    WEBSITE_RUN_FROM_PACKAGE = local.sas_url["java"]
    FUNCTIONS_WORKER_RUNTIME = "java"
  }
}
