"""Main CLI entry point"""

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def main():
    """kc-test - Testing CLI for Kong + Keycloak integration"""
    pass


@main.group()
def token():
    """JWT token operations"""
    pass


@token.command()
@click.option("--user", required=True, help="Username")
@click.option("--password", required=True, help="Password")
@click.option("--realm", default="kong-realm", help="Keycloak realm")
@click.option("--keycloak-url", default="http://localhost:8080", help="Keycloak URL")
def get(user, password, realm, keycloak_url):
    """Get JWT token for user"""
    from kc_test.keycloak_client import get_token

    console.print(f"[blue]Getting token for user:[/blue] {user}")
    console.print(f"[blue]Realm:[/blue] {realm}")

    # Get password from user
    # password = click.prompt("Password", hide_input=True)

    try:
        token_data = get_token(keycloak_url, realm, user, password)
        console.print(f"[green]✓ Token acquired successfully[/green]")
        console.print(f"\n[yellow]Access Token:[/yellow]\n{token_data['access_token']}")
        console.print(
            f"\n[yellow]Refresh Token:[/yellow]\n{token_data.get('refresh_token', 'N/A')}"
        )
        console.print(f"\n[blue]Expires in:[/blue] {token_data.get('expires_in', 'N/A')} seconds")
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise click.Abort()


@token.command()
@click.argument("token")
def decode(token):
    """Decode JWT token"""
    from kc_test.keycloak_client import decode_token

    try:
        payload = decode_token(token)

        table = Table(title="JWT Payload")
        table.add_column("Claim", style="cyan")
        table.add_column("Value", style="yellow")

        for key, value in payload.items():
            table.add_row(key, str(value))

        console.print(table)
    except Exception as e:
        console.print(f"[red]✗ Error decoding token:[/red] {e}")
        raise click.Abort()


@token.command()
@click.argument("refresh_token_str")
@click.option("--realm", default="kong-realm", help="Keycloak realm")
@click.option("--keycloak-url", default="http://localhost:8080", help="Keycloak URL")
def refresh(refresh_token_str, realm, keycloak_url):
    """Refresh JWT token"""
    from kc_test.keycloak_client import refresh_token

    console.print(f"[blue]Refreshing token for realm:[/blue] {realm}")

    try:
        token_data = refresh_token(keycloak_url, realm, refresh_token_str)
        console.print(f"[green]✓ Token refreshed successfully[/green]")
        console.print(f"\n[yellow]New Access Token:[/yellow]\n{token_data['access_token']}")
        console.print(
            f"\n[yellow]New Refresh Token:[/yellow]\n{token_data.get('refresh_token', 'N/A')}"
        )
        console.print(f"\n[blue]Expires in:[/blue] {token_data.get('expires_in', 'N/A')} seconds")
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise click.Abort()


@main.group()
def api():
    """API testing operations"""
    pass


@api.command()
@click.option("--endpoint", required=True, help="API endpoint", type=str)
@click.option("--token", help="JWT token")
@click.option("--kong-url", default="http://localhost:8000", help="Kong URL")
@click.option("--method", default="GET", help="HTTP method")
def call(endpoint, token, kong_url, method):
    """Call API endpoint"""
    from kc_test.api_tester import call_api

    console.print(f"[blue]Calling:[/blue] {method} {kong_url}/{endpoint}")

    try:
        response = call_api(kong_url, endpoint, method, token)
        console.print(f"[green]✓ Status:[/green] {response.status_code}")
        console.print(f"\n[yellow]Response:[/yellow]")
        console.print_json(data=response.json())
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise click.Abort()


@api.command()
@click.option("--suite", default="integration", help="Test suite name")
def test(suite):
    """Run API test suite"""
    from kc_test.api_tester import run_test_suite

    console.print(f"[blue]Running test suite:[/blue] {suite}")

    try:
        results = run_test_suite(suite)
        console.print(f"[green]✓ Tests passed:[/green] {results['passed']}")
        console.print(f"[red]✗ Tests failed:[/red] {results['failed']}")
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise click.Abort()


@main.group()
def suite():
    """Test suite operations"""
    pass


@suite.command()
@click.option("--env", default="dev", help="Environment")
@click.option("--keycloak-url", default="http://localhost:8080", help="Keycloak URL")
@click.option("--kong-url", default="http://localhost:8000", help="Kong URL")
@click.option("--output", default=None, help="Output file for report")
@click.option(
    "--format",
    default="console",
    type=click.Choice(["console", "json", "html", "markdown"]),
    help="Report format",
)
def run(env, keycloak_url, kong_url, output, format):
    """Run comprehensive test suite"""
    from kc_test.api_tester import run_comprehensive_suite
    from kc_test.reporter import generate_report

    console.print(f"[blue]Running comprehensive tests for environment:[/blue] {env}")

    try:
        results = run_comprehensive_suite(keycloak_url, kong_url, env)

        if format == "console":
            from kc_test.reporter import print_test_results, print_summary

            print_test_results(results["tests"])
            print_summary(results["passed"], results["failed"], results["total"])
        else:
            report = generate_report(results, format)
            if output:
                with open(output, "w") as f:
                    f.write(report)
                console.print(f"[green]✓ Report saved to:[/green] {output}")
            else:
                console.print(report)
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise click.Abort()


@main.group()
def keycloak():
    """Keycloak operations"""
    pass


@keycloak.command("list-users")
@click.option("--realm", default="kong-realm", help="Keycloak realm")
@click.option("--keycloak-url", default="http://localhost:8080", help="Keycloak URL")
@click.option("--admin-user", default="admin", help="Admin username")
def list_users(realm, keycloak_url, admin_user):
    """List users in realm"""
    from kc_test.keycloak_client import KeycloakAdmin

    console.print(f"[blue]Listing users in realm:[/blue] {realm}")
    admin_password = click.prompt("Admin Password", hide_input=True)

    try:
        admin = KeycloakAdmin(keycloak_url, admin_user, admin_password)
        users = admin.list_users(realm)

        table = Table(title=f"Users in {realm}")
        table.add_column("Username", style="cyan")
        table.add_column("Email", style="yellow")
        table.add_column("Enabled", style="green")
        table.add_column("ID", style="blue")

        for user in users:
            table.add_row(
                user.get("username", "N/A"),
                user.get("email", "N/A"),
                str(user.get("enabled", False)),
                user.get("id", "N/A")[:8] + "...",
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise click.Abort()


@keycloak.command("create-user")
@click.option("--realm", default="kong-realm", help="Keycloak realm")
@click.option("--username", required=True, help="Username")
@click.option("--email", help="Email")
@click.option("--keycloak-url", default="http://localhost:8080", help="Keycloak URL")
@click.option("--admin-user", default="admin", help="Admin username")
def create_user(realm, username, email, keycloak_url, admin_user):
    """Create user in realm"""
    from kc_test.keycloak_client import KeycloakAdmin

    console.print(f"[blue]Creating user in realm:[/blue] {realm}")
    admin_password = click.prompt("Admin Password", hide_input=True)
    user_password = click.prompt("User Password", hide_input=True)

    try:
        admin = KeycloakAdmin(keycloak_url, admin_user, admin_password)
        user_id = admin.create_user(realm, username, user_password, email)
        console.print(f"[green]✓ User created successfully[/green]")
        console.print(f"[blue]User ID:[/blue] {user_id}")
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise click.Abort()


@keycloak.command("assign-role")
@click.option("--realm", default="kong-realm", help="Keycloak realm")
@click.option("--username", required=True, help="Username")
@click.option("--role", required=True, help="Role name")
@click.option("--keycloak-url", default="http://localhost:8080", help="Keycloak URL")
@click.option("--admin-user", default="admin", help="Admin username")
def assign_role(realm, username, role, keycloak_url, admin_user):
    """Assign role to user"""
    from kc_test.keycloak_client import KeycloakAdmin

    console.print(f"[blue]Assigning role '{role}' to user '{username}' in realm:[/blue] {realm}")
    admin_password = click.prompt("Admin Password", hide_input=True)

    try:
        admin = KeycloakAdmin(keycloak_url, admin_user, admin_password)
        admin.assign_role(realm, username, role)
        console.print(f"[green]✓ Role assigned successfully[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise click.Abort()


@main.group()
def report():
    """Generate test reports"""
    pass


@report.command()
@click.option("--input", required=True, help="Input test results file (JSON)")
@click.option(
    "--format",
    default="html",
    type=click.Choice(["html", "markdown", "json"]),
    help="Report format",
)
@click.option("--output", required=True, help="Output file")
def generate(input, format, output):
    """Generate report from test results"""
    import json
    from kc_test.reporter import generate_report

    try:
        with open(input, "r") as f:
            results = json.load(f)

        report = generate_report(results, format)

        with open(output, "w") as f:
            f.write(report)

        console.print(f"[green]✓ Report generated:[/green] {output}")
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()
