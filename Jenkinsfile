pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set Up Python Environment') {
            steps {
                bat '''
                    python -m venv %VENV_DIR%
                    call %VENV_DIR%\\Scripts\\activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install requests
                '''
            }
        }

        stage('Train Model') {
            steps {
                bat '''
                    call %VENV_DIR%\\Scripts\\activate
                    python train_model.py
                '''
            }
        }

        stage('Start API & Smoke Test') {
            steps {
                bat '''
                    call %VENV_DIR%\\Scripts\\activate

                    rem Start Flask app in background and capture PID directly
                    powershell -Command "$p = Start-Process python app.py -RedirectStandardOutput app.log -NoNewWindow -PassThru; $p.Id | Out-File -FilePath app.pid -Encoding ascii"

                    echo Waiting for API to become ready...
                    powershell -Command "$ready=0; for ($i=0; $i -lt 30; $i++) { try { Invoke-WebRequest -Uri http://127.0.0.1:5000/ -UseBasicParsing | Out-Null; $ready=1; Write-Output 'API is up'; break } catch { Start-Sleep -Seconds 1 } }; if ($ready -eq 0) { Write-Output 'API did not start in time'; Get-Content app.log; exit 1 }"

                    python test_prediction.py
                '''
            }
        }
    }

    post {
        always {
            bat '''
                if exist app.pid (
                    for /F %%p in (app.pid) do taskkill /PID %%p /F
                    del app.pid
                )
                timeout /t 5 > nul
                python -c "import shutil; shutil.rmtree('%VENV_DIR%', ignore_errors=True)"
            '''
            archiveArtifacts artifacts: 'house_model.pkl, app.log, predictions.csv', allowEmptyArchive: true
        }
        success {
            echo 'Build, train, and smoke test succeeded.'
        }
        failure {
            echo 'Pipeline failed — check app.log and the console output above for details.'
        }
    }
}
