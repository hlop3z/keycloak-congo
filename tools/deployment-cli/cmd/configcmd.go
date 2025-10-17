package cmd

import (
	"fmt"

	"github.com/hlop3z/keycloak-congo/tools/deployment-cli/pkg/config"
	"github.com/hlop3z/keycloak-congo/tools/deployment-cli/pkg/validate"
	"github.com/spf13/cobra"
)

// configCmd represents the config command
var configCmd = &cobra.Command{
	Use:   "config",
	Short: "Configuration management",
	Long:  `Manage deployment configuration`,
}

var configValidateCmd = &cobra.Command{
	Use:   "validate",
	Short: "Validate configuration",
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		fmt.Println("Validating configuration...")

		// Validate project structure
		if err := validate.ValidateProjectStructure(cfg.GetProjectRoot()); err != nil {
			return fmt.Errorf("project structure validation failed: %w", err)
		}
		fmt.Println("✓ Project structure is valid")

		// Validate compose files
		composeFiles := []string{
			"compose/docker-compose.full.yml",
			"infrastructure/keycloak/docker-compose.yml",
			"infrastructure/kong/docker-compose.yml",
		}

		for _, file := range composeFiles {
			fullPath := cfg.GetProjectRoot() + "/" + file
			if err := validate.ValidateComposeFile(fullPath); err != nil {
				fmt.Printf("⚠ Warning: %s validation failed: %v\n", file, err)
			} else {
				fmt.Printf("✓ %s is valid\n", file)
			}
		}

		fmt.Println("\n✓ Configuration validation completed")
		return nil
	},
}

var configShowCmd = &cobra.Command{
	Use:   "show",
	Short: "Show current configuration",
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		fmt.Println("Current Configuration:")
		fmt.Println("---------------------")
		fmt.Printf("Project Root:        %s\n", cfg.ProjectRoot)
		fmt.Printf("Default Environment: %s\n", cfg.DefaultEnvironment)
		fmt.Printf("Kong Instances:      %d\n", len(cfg.KongInstances))

		for i, instance := range cfg.KongInstances {
			fmt.Printf("\n  Instance %d:\n", i+1)
			fmt.Printf("    Name:  %s\n", instance.Name)
			fmt.Printf("    Realm: %s\n", instance.Realm)
			fmt.Printf("    Port:  %d\n", instance.Port)
		}

		return nil
	},
}

var configInitCmd = &cobra.Command{
	Use:   "init",
	Short: "Initialize default configuration",
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg := config.GetDefaultConfig()

		configPath := cfgFile
		if configPath == "" {
			configPath = config.DefaultConfigPath()
		}

		if err := config.SaveConfig(cfg, configPath); err != nil {
			return fmt.Errorf("failed to save config: %w", err)
		}

		fmt.Printf("✓ Configuration initialized at: %s\n", configPath)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(configCmd)
	configCmd.AddCommand(configValidateCmd)
	configCmd.AddCommand(configShowCmd)
	configCmd.AddCommand(configInitCmd)
}
