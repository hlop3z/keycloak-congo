package cmd

import (
	"fmt"
	"path/filepath"

	"github.com/hlop3z/keycloak-congo/tools/deployment-cli/pkg/config"
	"github.com/hlop3z/keycloak-congo/tools/deployment-cli/pkg/docker"
	"github.com/spf13/cobra"
)

var (
	removeVolumes bool
	envFlagDown   string
)

// downCmd represents the down command
var downCmd = &cobra.Command{
	Use:   "down [component|all]",
	Short: "Stop components",
	Long:  `Stop and remove docker-compose services`,
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		projectRoot := cfg.GetProjectRoot()
		dc := docker.NewDockerCompose(projectRoot, verbose)

		// Set env file based on environment (use envFlagDown if available)
		env := envFlagDown
		if env == "" {
			env = "dev"
		}
		envFile := filepath.Join(projectRoot, "compose", "environments", env+".env")
		dc.EnvFile = envFile

		if len(args) == 0 || args[0] == "all" {
			// Stop all components
			fmt.Println("Stopping all components...")

			components := []struct {
				name string
				file string
			}{
				{"full stack", filepath.Join(projectRoot, "compose", "docker-compose.full.yml")},
				{"multi-kong", filepath.Join(projectRoot, "compose", "docker-compose.multi-kong.yml")},
				{"kong", filepath.Join(projectRoot, "infrastructure", "kong", "docker-compose.yml")},
				{"keycloak", filepath.Join(projectRoot, "infrastructure", "keycloak", "docker-compose.yml")},
			}

			for _, comp := range components {
				fmt.Printf("Stopping %s...\n", comp.name)
				if err := dc.Down(comp.file, removeVolumes); err != nil {
					fmt.Printf("  Warning: Failed to stop %s: %v\n", comp.name, err)
				} else {
					fmt.Printf("  ✓ %s stopped\n", comp.name)
				}
			}

			fmt.Println("✓ All components stopped")
			return nil
		}

		// Stop specific component
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

		fmt.Printf("Stopping %s...\n", component)
		if err := dc.Down(composeFile, removeVolumes); err != nil {
			return fmt.Errorf("failed to stop %s: %w", component, err)
		}

		fmt.Printf("✓ %s stopped successfully!\n", component)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(downCmd)
	downCmd.Flags().BoolVar(&removeVolumes, "volumes", false, "Remove volumes")
	downCmd.Flags().StringVar(&envFlagDown, "env", "dev", "environment (dev/prod)")
}
