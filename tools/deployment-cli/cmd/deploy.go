package cmd

import (
	"fmt"
	"path/filepath"

	"github.com/hlop3z/keycloak-congo/tools/deployment-cli/pkg/config"
	"github.com/hlop3z/keycloak-congo/tools/deployment-cli/pkg/docker"
	"github.com/spf13/cobra"
)

var (
	envFlag string
)

// deployCmd represents the deploy command
var deployCmd = &cobra.Command{
	Use:   "deploy [component]",
	Short: "Deploy components",
	Long: `Deploy Kong + Keycloak components.

Components:
- keycloak: Deploy Keycloak + PostgreSQL
- kong: Deploy Kong instance
- full: Deploy all components
- multi-kong: Deploy multiple Kong instances`,
}

var fullCmd = &cobra.Command{
	Use:   "full",
	Short: "Deploy full stack",
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		projectRoot := cfg.GetProjectRoot()
		dc := docker.NewDockerCompose(projectRoot, verbose)

		fmt.Println("Deploying full stack...")
		fmt.Printf("Environment: %s\n", envFlag)
		fmt.Printf("Project Root: %s\n", projectRoot)

		composeFile := filepath.Join(projectRoot, "compose", "docker-compose.full.yml")

		if err := dc.Up(composeFile, true); err != nil {
			return fmt.Errorf("failed to deploy full stack: %w", err)
		}

		fmt.Println("✓ Full stack deployed successfully!")
		return nil
	},
}

var keycloakCmd = &cobra.Command{
	Use:   "keycloak",
	Short: "Deploy Keycloak",
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		projectRoot := cfg.GetProjectRoot()
		dc := docker.NewDockerCompose(projectRoot, verbose)

		fmt.Println("Deploying Keycloak...")
		fmt.Printf("Project Root: %s\n", projectRoot)

		composeFile := filepath.Join(projectRoot, "infrastructure", "keycloak", "docker-compose.yml")

		if err := dc.Up(composeFile, true); err != nil {
			return fmt.Errorf("failed to deploy Keycloak: %w", err)
		}

		fmt.Println("✓ Keycloak deployed successfully!")
		return nil
	},
}

var kongCmd = &cobra.Command{
	Use:   "kong",
	Short: "Deploy Kong",
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		projectRoot := cfg.GetProjectRoot()
		dc := docker.NewDockerCompose(projectRoot, verbose)

		fmt.Println("Deploying Kong...")
		fmt.Printf("Project Root: %s\n", projectRoot)

		composeFile := filepath.Join(projectRoot, "infrastructure", "kong", "docker-compose.yml")

		if err := dc.Up(composeFile, true); err != nil {
			return fmt.Errorf("failed to deploy Kong: %w", err)
		}

		fmt.Println("✓ Kong deployed successfully!")
		return nil
	},
}

var multiKongCmd = &cobra.Command{
	Use:   "multi-kong",
	Short: "Deploy multiple Kong instances",
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		projectRoot := cfg.GetProjectRoot()
		dc := docker.NewDockerCompose(projectRoot, verbose)

		fmt.Println("Deploying multiple Kong instances...")
		fmt.Printf("Project Root: %s\n", projectRoot)

		composeFile := filepath.Join(projectRoot, "compose", "docker-compose.multi-kong.yml")

		if err := dc.Up(composeFile, true); err != nil {
			return fmt.Errorf("failed to deploy multi-Kong: %w", err)
		}

		fmt.Println("✓ Multiple Kong instances deployed successfully!")
		return nil
	},
}

func init() {
	rootCmd.AddCommand(deployCmd)
	deployCmd.AddCommand(fullCmd)
	deployCmd.AddCommand(keycloakCmd)
	deployCmd.AddCommand(kongCmd)
	deployCmd.AddCommand(multiKongCmd)

	deployCmd.PersistentFlags().StringVar(&envFlag, "env", "dev", "environment (dev/prod)")
}
