pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        API_IMAGE = 'house-price-prediction'
        UI_IMAGE  = 'house-price-ui'
        IMAGE_TAG = 'latest'
        VERSION_TAG = "${BUILD_NUMBER}"
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
                '''
            }
        }

        stage('Build API Image') {
            steps {
                bat '''
                    docker build -t %DOCKER_REGISTRY%/%API_IMAGE%:%VERSION_TAG% -t %DOCKER_REGISTRY%/%API_IMAGE%:%IMAGE_TAG% -f Dockerfile.api .
                '''
            }
        }

        stage('Build UI Image') {
            steps {
                bat '''
                    docker build -t %DOCKER_REGISTRY%/%UI_IMAGE%:%VERSION_TAG% -t %DOCKER_REGISTRY%/%UI_IMAGE%:%IMAGE_TAG% -f Dockerfile.streamlit .
                '''
            }
        }

        stage('Push Images') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat '''
                        echo Logging in to DockerHub...
                        docker login -u %DOCKER_USER% -p %DOCKER_PASS%

                        docker push %DOCKER_REGISTRY%/%API_IMAGE%:%VERSION_TAG%
                        docker push %DOCKER_REGISTRY%/%API_IMAGE%:%IMAGE_TAG%

                        docker push %DOCKER_REGISTRY%/%UI_IMAGE%:%VERSION_TAG%
                        docker push %DOCKER_REGISTRY%/%UI_IMAGE%:%IMAGE_TAG%
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
            echo 'Build, train, smoke test, API image and UI image build + push succeeded.'
        }
        failure {
            echo 'Pipeline failed — check app.log and console output for details.'
        }
    }
}
