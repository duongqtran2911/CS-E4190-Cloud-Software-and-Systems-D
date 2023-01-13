terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.5.0"
    }
  }
}

provider "google" {
  #credentials = file("newtest-363815-859ec40e2556.json")
  project = "newtest-363815"
  region  = "europe-north1"
  zone    = "europe-north1-a"
}

variable "vm_name_input" {
  default = "exercise-2-vm"
}

# Create vm_instance
resource "google_compute_instance" "vm_instance" {
  name         = var.vm_name_input
  machine_type = "f1-micro"
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
    }
  }

  network_interface {
    network = "terraform-network1"
    access_config {
    }
  }
}

output "vm_name" {
  value = google_compute_instance.vm_instance.name
}

output "public_ip" {
  value = google_compute_instance.vm_instance.network_interface.0.access_config.0.nat_ip
}

