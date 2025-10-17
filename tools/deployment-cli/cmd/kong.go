package cmd

import (
	"fmt"

	"github.com/hlop3z/keycloak-congo/tools/deployment-cli/pkg/config"
	"github.com/spf13/cobra"
)

var (
	kongName  string
	kongRealm string
	kongPort  int
)

// kongManageCmd represents the kong management command
var kongManageCmd = &cobra.Command{
	Use:   "kong",
	Short: "Manage Kong instances",
	Long:  `Add, remove, list, and manage Kong instances`,
}

var kongAddCmd = &cobra.Command{
	Use:   "add",
	Short: "Add new Kong instance",
	RunE: func(cmd *cobra.Command, args []string) error {
		if kongName == "" {
			return fmt.Errorf("--name is required")
		}
		if kongRealm == "" {
			return fmt.Errorf("--realm is required")
		}

		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		instance := config.KongInstance{
			Name:  kongName,
			Realm: kongRealm,
			Port:  kongPort,
		}

		if err := cfg.AddKongInstance(instance); err != nil {
			return fmt.Errorf("failed to add Kong instance: %w", err)
		}

		if err := config.SaveConfig(cfg, cfgFile); err != nil {
			return fmt.Errorf("failed to save config: %w", err)
		}

		fmt.Printf("✓ Kong instance '%s' added successfully!\n", kongName)
		fmt.Printf("  Realm: %s\n", kongRealm)
		fmt.Printf("  Port: %d\n", kongPort)
		return nil
	},
}

var kongRemoveCmd = &cobra.Command{
	Use:   "remove",
	Short: "Remove Kong instance",
	RunE: func(cmd *cobra.Command, args []string) error {
		if kongName == "" {
			return fmt.Errorf("--name is required")
		}

		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		if err := cfg.RemoveKongInstance(kongName); err != nil {
			return fmt.Errorf("failed to remove Kong instance: %w", err)
		}

		if err := config.SaveConfig(cfg, cfgFile); err != nil {
			return fmt.Errorf("failed to save config: %w", err)
		}

		fmt.Printf("✓ Kong instance '%s' removed successfully!\n", kongName)
		return nil
	},
}

var kongListCmd = &cobra.Command{
	Use:   "list",
	Short: "List Kong instances",
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		if len(cfg.KongInstances) == 0 {
			fmt.Println("No Kong instances configured")
			return nil
		}

		fmt.Println("Kong Instances:")
		fmt.Println("---------------")
		for _, instance := range cfg.KongInstances {
			fmt.Printf("  Name:  %s\n", instance.Name)
			fmt.Printf("  Realm: %s\n", instance.Realm)
			fmt.Printf("  Port:  %d\n", instance.Port)
			fmt.Println()
		}

		return nil
	},
}

func init() {
	rootCmd.AddCommand(kongManageCmd)
	kongManageCmd.AddCommand(kongAddCmd)
	kongManageCmd.AddCommand(kongRemoveCmd)
	kongManageCmd.AddCommand(kongListCmd)

	kongAddCmd.Flags().StringVar(&kongName, "name", "", "Kong instance name")
	kongAddCmd.Flags().StringVar(&kongRealm, "realm", "", "Keycloak realm")
	kongAddCmd.Flags().IntVar(&kongPort, "port", 8000, "Kong port")

	kongRemoveCmd.Flags().StringVar(&kongName, "name", "", "Kong instance name")
}
