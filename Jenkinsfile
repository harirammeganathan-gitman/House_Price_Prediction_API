pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        IMAGE_NAME = 'house-price-prediction'
        IMAGE_TAG = 'latest'
        VERSION_TAG = "${BUILD_NUMBER}" // auto-generated version tag based on Jenkins build number
        DOCKER_REGISTRY = 'hrmddocker'   // your DockerHub username
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

                    rem Start Flask app in background and capture PID
                    powershell -Command "$p = Start-Process python app.py -RedirectStandardOutput app.log -NoNewWindow -PassThru; $p.Id | Out-File -FilePath app.pid -Encoding ascii"

                    echo Waiting for API to become ready...
                    powershell -Command "$ready=0; for ($i=0; $i -lt 30; $i++) { try { Invoke-WebRequest -Uri http://127.0.0.1:5000/ -UseBasicParsing | Out-Null; $ready=1; Write-Output 'API is up'; break } catch { Start-Sleep -Seconds 1 } }; if ($ready -eq 0) { Write-Output 'API did not start in time'; Get-Content app.log; exit 1 }"

                    python test_prediction.py
                '''
            }
        }

        stage('Debug Docker Environment') {
            steps {
                bat '''
                    echo Checking Docker installation...
                    docker --version
                    docker info
                    dir
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                    docker build -t %IMAGE_NAME%:%IMAGE_TAG% .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat '''
                        echo Logging in to DockerHub...
                        docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                        docker tag %IMAGE_NAME%:%IMAGE_TAG% %DOCKER_REGISTRY%/%IMAGE_NAME%:%IMAGE_TAG%
                        docker tag %IMAGE_NAME%:%IMAGE_TAG% %DOCKER_REGISTRY%/%IMAGE_NAME%:%VERSION_TAG%
                        docker push %DOCKER_REGISTRY%/%IMAGE_NAME%:%IMAGE_TAG%
                        docker push %DOCKER_REGISTRY%/%IMAGE_NAME%:%VERSION_TAG%
                    '''
                }
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
            echo 'Build, train, smoke test, Docker debug, image build and push succeeded.'
        }
        failure {
            echo 'Pipeline failed — check app.log and the console output above for details.'
        }
    }
}
