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

                    rem Start Flask app in background and capture PID properly
                    powershell -Command "Start-Process python app.py -RedirectStandardOutput app.log -NoNewWindow; (Get-Process -Name python | Select -First 1 -ExpandProperty Id) | Out-File -FilePath app.pid -Encoding ascii"

                    echo Waiting for API to become ready...
                    set ready=0

                    for /L %%i in (1,1,30) do (
                        curl http://127.0.0.1:5000/ > nul 2>&1
                        if %%ERRORLEVEL%%==0 (
                            set ready=1
                            echo API is up
                            goto ready
                        )
                        timeout /t 1 > nul
                    )
                    :ready

                    if %ready%==0 (
                        echo API did not start in time
                        type app.log
                        exit /b 1
                    )

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
                rmdir /S /Q %VENV_DIR%
            '''
            archiveArtifacts artifacts: 'house_model.pkl, app.log', allowEmptyArchive: true
        }
        success {
            echo 'Build, train, and smoke test succeeded.'
        }
        failure {
            echo 'Pipeline failed — check app.log and the console output above for details.'
        }
    }
}
