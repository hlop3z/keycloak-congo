package docker

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// DockerCompose handles docker-compose operations
type DockerCompose struct {
	ProjectRoot string
	Verbose     bool
	EnvFile     string
}

// NewDockerCompose creates a new DockerCompose instance
func NewDockerCompose(projectRoot string, verbose bool) *DockerCompose {
	return &DockerCompose{
		ProjectRoot: projectRoot,
		Verbose:     verbose,
	}
}

// Up starts docker-compose services
func (dc *DockerCompose) Up(composeFile string, detach bool) error {
	args := []string{"compose", "-f", composeFile}

	// Add env file if specified
	if dc.EnvFile != "" {
		args = append(args, "--env-file", dc.EnvFile)
	}

	args = append(args, "up")
	if detach {
		args = append(args, "-d")
	}

	return dc.runDockerCommand(args...)
}

// Down stops docker-compose services
func (dc *DockerCompose) Down(composeFile string, volumes bool) error {
	args := []string{"compose", "-f", composeFile}

	// Add env file if specified
	if dc.EnvFile != "" {
		args = append(args, "--env-file", dc.EnvFile)
	}

	args = append(args, "down")
	if volumes {
		args = append(args, "-v")
	}

	return dc.runDockerCommand(args...)
}

// Logs displays logs from docker-compose services
func (dc *DockerCompose) Logs(composeFile string, service string, follow bool, tail int) error {
	args := []string{"compose", "-f", composeFile, "logs"}

	if follow {
		args = append(args, "-f")
	}

	if tail > 0 {
		args = append(args, "--tail", fmt.Sprintf("%d", tail))
	}

	if service != "" {
		args = append(args, service)
	}

	return dc.runDockerCommand(args...)
}

// Status checks the status of docker-compose services
func (dc *DockerCompose) Status(composeFile string) error {
	args := []string{"compose", "-f", composeFile, "ps"}
	return dc.runDockerCommand(args...)
}

// Build builds docker-compose services
func (dc *DockerCompose) Build(composeFile string, service string) error {
	args := []string{"compose", "-f", composeFile, "build"}

	if service != "" {
		args = append(args, service)
	}

	return dc.runDockerCommand(args...)
}

// Exec executes a command in a running container
func (dc *DockerCompose) Exec(composeFile string, service string, command []string) error {
	args := []string{"compose", "-f", composeFile, "exec", service}
	args = append(args, command...)

	return dc.runDockerCommand(args...)
}

// Pull pulls docker images
func (dc *DockerCompose) Pull(composeFile string) error {
	args := []string{"compose", "-f", composeFile, "pull"}
	return dc.runDockerCommand(args...)
}

// IsRunning checks if a compose project is running
func (dc *DockerCompose) IsRunning(composeFile string) (bool, error) {
	cmd := exec.Command("docker", "compose", "-f", composeFile, "ps", "-q")
	output, err := cmd.Output()
	if err != nil {
		return false, err
	}

	return len(strings.TrimSpace(string(output))) > 0, nil
}

// GetComposeFilePath returns the absolute path to a compose file
func (dc *DockerCompose) GetComposeFilePath(relativePath string) string {
	return filepath.Join(dc.ProjectRoot, relativePath)
}

// runDockerCommand executes a docker command
func (dc *DockerCompose) runDockerCommand(args ...string) error {
	cmd := exec.Command("docker", args...)

	if dc.Verbose {
		fmt.Printf("Executing: docker %s\n", strings.Join(args, " "))
	}

	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin

	return cmd.Run()
}

// Restart restarts docker-compose services
func (dc *DockerCompose) Restart(composeFile string, service string) error {
	args := []string{"compose", "-f", composeFile, "restart"}

	if service != "" {
		args = append(args, service)
	}

	return dc.runDockerCommand(args...)
}

// Stop stops docker-compose services without removing them
func (dc *DockerCompose) Stop(composeFile string, service string) error {
	args := []string{"compose", "-f", composeFile, "stop"}

	if service != "" {
		args = append(args, service)
	}

	return dc.runDockerCommand(args...)
}
