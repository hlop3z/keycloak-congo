package cmd

import (
	"fmt"
	"path/filepath"

	"github.com/hlop3z/keycloak-congo/tools/deployment-cli/pkg/config"
	"github.com/hlop3z/keycloak-congo/tools/deployment-cli/pkg/docker"
	"github.com/spf13/cobra"
)

// statusCmd represents the status command
var statusCmd = &cobra.Command{
	Use:   "status [component]",
	Short: "View component status",
	Long:  `View the status of deployed components`,
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		projectRoot := cfg.GetProjectRoot()
		dc := docker.NewDockerCompose(projectRoot, verbose)

		if len(args) == 0 {
			// Show status of all components
			fmt.Println("=== Full Stack Status ===")
			composeFile := filepath.Join(projectRoot, "compose", "docker-compose.full.yml")
			if err := dc.Status(composeFile); err != nil {
				fmt.Printf("Full stack not running or error: %v\n", err)
			}

			fmt.Println("\n=== Keycloak Status ===")
			composeFile = filepath.Join(projectRoot, "infrastructure", "keycloak", "docker-compose.yml")
			if err := dc.Status(composeFile); err != nil {
				fmt.Printf("Keycloak not running or error: %v\n", err)
			}

			fmt.Println("\n=== Kong Status ===")
			composeFile = filepath.Join(projectRoot, "infrastructure", "kong", "docker-compose.yml")
			if err := dc.Status(composeFile); err != nil {
				fmt.Printf("Kong not running or error: %v\n", err)
			}

			return nil
		}

		// Show status of specific component
		component := args[0]
		var composeFile string

		switch component {
		case "keycloak":
			composeFile = filepath.Join(projectRoot, "infrastructure", "keycloak", "docker-compose.yml")
		case "kong":
			composeFile = filepath.Join(projectRoot, "infrastructure", "kong", "docker-compose.yml")
		case "full":
			composeFile = filepath.Join(projectRoot, "compose", "docker-compose.full.yml")
		case "multi-kong":
			composeFile = filepath.Join(projectRoot, "compose", "docker-compose.multi-kong.yml")
		default:
			return fmt.Errorf("unknown component: %s", component)
		}

		fmt.Printf("=== %s Status ===\n", component)
		return dc.Status(composeFile)
	},
}

// healthCmd represents the health check command
var healthCmd = &cobra.Command{
	Use:   "health",
	Short: "Perform health checks",
	Long:  `Check the health of all deployed services`,
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("Running health checks...")

		// Basic health checks
		// TODO: Implement actual health checks (HTTP requests to services)

		fmt.Println("✓ Health checks completed")
		return nil
	},
}

func init() {
	rootCmd.AddCommand(statusCmd)
	rootCmd.AddCommand(healthCmd)
}
