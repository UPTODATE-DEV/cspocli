@echo off
REM Cardano SPO CLI - Script d'installation pour Windows

echo 🚀 Installation de Cardano SPO CLI...

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH.
    echo    Veuillez installer Python depuis https://python.org
    echo    Assurez-vous de cocher "Add Python to PATH" lors de l'installation
    pause
    exit /b 1
)

REM Vérifier pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip n'est pas installé.
    pause
    exit /b 1
)

echo ✅ Python et pip détectés

REM Installer les dépendances
echo 📦 Installation des dépendances...
python -m pip install --user requests click cryptography mnemonic bech32 colorama tqdm

REM Installer le CLI
echo 🔧 Installation du CLI...
python -m pip install --user -e .

echo.
echo 🎉 Installation terminée !
echo.
echo 📖 Utilisation :
echo    python -m cardano_spo_cli --ticker MYPOOL --purpose pledge
echo    python -m cardano_spo_cli --help
echo.
echo 💡 Pour plus d'informations, consultez le README.md
echo.
pause # Windows install
