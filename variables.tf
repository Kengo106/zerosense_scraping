variable "api_key" {
  description = "Google Cloud service account key JSON"
  type        = string
}
variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_user" {
  description = "Database user"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
}
variable "db_host" {
  description = "Database host"
  type        = string
}
variable "django_debug" {
  description = "django debug"
  type        = string
}

