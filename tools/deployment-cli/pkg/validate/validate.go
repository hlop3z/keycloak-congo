package validate

import (
	"fmt"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"
)

// ValidateComposeFile validates a docker-compose file
func ValidateComposeFile(filePath string) error {
	// Check if file exists
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		return fmt.Errorf("compose file does not exist: %s", filePath)
	}

	// Try to parse as YAML
	data, err := os.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("failed to read compose file: %w", err)
	}

	var composeContent map[string]interface{}
	if err := yaml.Unmarshal(data, &composeContent); err != nil {
		return fmt.Errorf("invalid YAML in compose file: %w", err)
	}

	// Check for required fields
	if _, ok := composeContent["services"]; !ok {
		return fmt.Errorf("compose file missing 'services' section")
	}

	return nil
}

// ValidateRealmFile validates a Keycloak realm configuration file
func ValidateRealmFile(filePath string) error {
	// Check if file exists
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		return fmt.Errorf("realm file does not exist: %s", filePath)
	}

	// Try to parse as JSON (Keycloak realm files are JSON)
	data, err := os.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("failed to read realm file: %w", err)
	}

	// Basic validation - just check if it's valid JSON
	var realmContent map[string]interface{}
	if err := yaml.Unmarshal(data, &realmContent); err != nil {
		return fmt.Errorf("invalid JSON in realm file: %w", err)
	}

	// Check for required realm fields
	if _, ok := realmContent["realm"]; !ok {
		return fmt.Errorf("realm file missing 'realm' field")
	}

	return nil
}

// ValidateProjectStructure validates the project directory structure
func ValidateProjectStructure(projectRoot string) error {
	requiredDirs := []string{
		"infrastructure/keycloak",
		"infrastructure/kong",
		"compose",
	}

	for _, dir := range requiredDirs {
		fullPath := filepath.Join(projectRoot, dir)
		if _, err := os.Stat(fullPath); os.IsNotExist(err) {
			return fmt.Errorf("required directory not found: %s", dir)
		}
	}

	return nil
}

// ValidateDockerInstallation checks if Docker is installed and running
func ValidateDockerInstallation() error {
	// This would need to actually check Docker - placeholder for now
	return nil
}
