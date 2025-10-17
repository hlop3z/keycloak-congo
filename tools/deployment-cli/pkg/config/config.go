package config

import (
	"fmt"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"
)

// Config represents the deployment configuration
type Config struct {
	ProjectRoot        string         `yaml:"project_root"`
	DefaultEnvironment string         `yaml:"default_environment"`
	KongInstances      []KongInstance `yaml:"kong_instances"`
}

// KongInstance represents a Kong instance configuration
type KongInstance struct {
	Name  string `yaml:"name"`
	Realm string `yaml:"realm"`
	Port  int    `yaml:"port"`
}

// DefaultConfigPath returns the default config file path
func DefaultConfigPath() string {
	home, err := os.UserHomeDir()
	if err != nil {
		return ".kc-deploy.yaml"
	}
	return filepath.Join(home, ".kc-deploy.yaml")
}

// LoadConfig loads configuration from file
func LoadConfig(configFile string) (*Config, error) {
	if configFile == "" {
		configFile = DefaultConfigPath()
	}

	// If config doesn't exist, return default config
	if _, err := os.Stat(configFile); os.IsNotExist(err) {
		return GetDefaultConfig(), nil
	}

	data, err := os.ReadFile(configFile)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var config Config
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse config file: %w", err)
	}

	return &config, nil
}

// SaveConfig saves configuration to file
func SaveConfig(config *Config, configFile string) error {
	if configFile == "" {
		configFile = DefaultConfigPath()
	}

	data, err := yaml.Marshal(config)
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	// Ensure directory exists
	dir := filepath.Dir(configFile)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create config directory: %w", err)
	}

	if err := os.WriteFile(configFile, data, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}

// GetDefaultConfig returns default configuration
func GetDefaultConfig() *Config {
	// Try to get project root from current working directory
	cwd, err := os.Getwd()
	if err != nil {
		cwd = "."
	}

	return &Config{
		ProjectRoot:        cwd,
		DefaultEnvironment: "dev",
		KongInstances: []KongInstance{
			{
				Name:  "kong-public",
				Realm: "kong-realm",
				Port:  8000,
			},
			{
				Name:  "kong-internal",
				Realm: "internal-realm",
				Port:  9000,
			},
		},
	}
}

// GetProjectRoot returns the project root directory
func (c *Config) GetProjectRoot() string {
	if c.ProjectRoot != "" {
		return c.ProjectRoot
	}

	// Try environment variable
	if root := os.Getenv("KC_DEPLOY_PROJECT_ROOT"); root != "" {
		return root
	}

	// Use current directory
	cwd, err := os.Getwd()
	if err != nil {
		return "."
	}
	return cwd
}

// FindKongInstance finds a Kong instance by name
func (c *Config) FindKongInstance(name string) (*KongInstance, error) {
	for _, instance := range c.KongInstances {
		if instance.Name == name {
			return &instance, nil
		}
	}
	return nil, fmt.Errorf("Kong instance '%s' not found", name)
}

// AddKongInstance adds a new Kong instance
func (c *Config) AddKongInstance(instance KongInstance) error {
	// Check if instance with same name already exists
	for _, existing := range c.KongInstances {
		if existing.Name == instance.Name {
			return fmt.Errorf("Kong instance with name '%s' already exists", instance.Name)
		}
	}

	c.KongInstances = append(c.KongInstances, instance)
	return nil
}

// RemoveKongInstance removes a Kong instance by name
func (c *Config) RemoveKongInstance(name string) error {
	for i, instance := range c.KongInstances {
		if instance.Name == name {
			c.KongInstances = append(c.KongInstances[:i], c.KongInstances[i+1:]...)
			return nil
		}
	}
	return fmt.Errorf("Kong instance '%s' not found", name)
}
