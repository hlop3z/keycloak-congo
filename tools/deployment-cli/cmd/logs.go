package cmd

import (
	"fmt"
	"path/filepath"

	"github.com/hlop3z/keycloak-congo/tools/deployment-cli/pkg/config"
	"github.com/hlop3z/keycloak-congo/tools/deployment-cli/pkg/docker"
	"github.com/spf13/cobra"
)

var (
	followLogs bool
	tailLines  int
)

// logsCmd represents the logs command
var logsCmd = &cobra.Command{
	Use:   "logs [component] [service]",
	Short: "View logs",
	Long:  `View logs from docker-compose services`,
	RunE: func(cmd *cobra.Command, args []string) error {
		if len(args) == 0 {
			return fmt.Errorf("component is required (keycloak, kong, full, multi-kong)")
		}

		cfg, err := config.LoadConfig(cfgFile)
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		projectRoot := cfg.GetProjectRoot()
		dc := docker.NewDockerCompose(projectRoot, verbose)

		component := args[0]
		service := ""
		if len(args) > 1 {
			service = args[1]
		}

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

		return dc.Logs(composeFile, service, followLogs, tailLines)
	},
}

func init() {
	rootCmd.AddCommand(logsCmd)
	logsCmd.Flags().BoolVarP(&followLogs, "follow", "f", false, "Follow log output")
	logsCmd.Flags().IntVar(&tailLines, "tail", 100, "Number of lines to show from the end")
}
