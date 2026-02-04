"""
Configuración de pytest con generación automática de badges.
"""


def pytest_sessionfinish(session, exitstatus):
    """Hook que se ejecuta al finalizar todos los tests para generar los badges."""
    import subprocess
    import sys
    import os

    # Crear carpeta badges si no existe
    badges_dir = "badges"
    os.makedirs(badges_dir, exist_ok=True)

    # Solo generar badges si los tests se ejecutaron (no errores de configuración)
    if exitstatus in (0, 1):
        # Generar badge de coverage
        try:
            subprocess.run(
                [sys.executable, "-m", "coverage_badge", "-o", f"{badges_dir}/coverage.svg", "-f"],
                check=True,
                capture_output=True
            )
            print(f"\n✓ Badge de coverage actualizado en {badges_dir}/coverage.svg")
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(
                    ["coverage-badge", "-o", f"{badges_dir}/coverage.svg", "-f"],
                    check=True,
                    capture_output=True
                )
                print(f"\n✓ Badge de coverage actualizado en {badges_dir}/coverage.svg")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("\n⚠ No se pudo generar el badge de coverage")

        # Generar badge de tests
        try:
            subprocess.run(
                [sys.executable, "-m", "genbadge", "tests", "-i", "test-results.xml", "-o", f"{badges_dir}/tests.svg"],
                check=True,
                capture_output=True
            )
            print(f"✓ Badge de tests actualizado en {badges_dir}/tests.svg")
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(
                    ["genbadge", "tests", "-i", "test-results.xml", "-o", f"{badges_dir}/tests.svg"],
                    check=True,
                    capture_output=True
                )
                print(f"✓ Badge de tests actualizado en {badges_dir}/tests.svg")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠ No se pudo generar el badge de tests")
