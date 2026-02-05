pipeline {
    agent any

    environment {
        // Python virtual environment path
        VENV_PATH = "${WORKSPACE}/venv"
        // Reports directory
        REPORTS_DIR = "${WORKSPACE}/reports"
        // Test pass rate threshold (percentage)
        TEST_PASS_THRESHOLD = 80
    }

    triggers {
        // Trigger build on GitHub push events
        githubPush()
    }

    options {
        // Keep only last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Timeout after 30 minutes
        timeout(time: 30, unit: 'MINUTES')
        // Add timestamps to console output
        timestamps()
        // Disable concurrent builds
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                sh '''
                    python3 -m venv ${VENV_PATH}
                    . ${VENV_PATH}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Create Reports Directory') {
            steps {
                sh 'mkdir -p ${REPORTS_DIR}'
            }
        }

        // ==================== QUALITY GATES ====================

        stage('Quality Gate: Code Linting') {
            steps {
                echo 'Running code linting with flake8 and pylint...'
                sh '''
                    . ${VENV_PATH}/bin/activate

                    # Flake8 - PEP8 style checker
                    flake8 Pages/ tests/ Utilities/ \
                        --max-line-length=120 \
                        --exclude=__pycache__,venv \
                        --format=default \
                        --output-file=${REPORTS_DIR}/flake8-report.txt \
                        --tee || true

                    # Pylint - Code quality checker
                    pylint Pages/ tests/ Utilities/ \
                        --exit-zero \
                        --output-format=text \
                        --reports=y \
                        > ${REPORTS_DIR}/pylint-report.txt || true
                '''
            }
            post {
                always {
                    // Archive linting reports
                    archiveArtifacts artifacts: 'reports/*lint*.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Quality Gate: Security Scan') {
            steps {
                echo 'Running security scans with bandit and safety...'
                sh '''
                    . ${VENV_PATH}/bin/activate

                    # Bandit - Python security linter
                    bandit -r Pages/ tests/ Utilities/ \
                        -f json \
                        -o ${REPORTS_DIR}/bandit-report.json \
                        --exit-zero || true

                    bandit -r Pages/ tests/ Utilities/ \
                        -f txt \
                        -o ${REPORTS_DIR}/bandit-report.txt \
                        --exit-zero || true

                    # Safety - Check dependencies for known vulnerabilities
                    safety check \
                        --output json \
                        > ${REPORTS_DIR}/safety-report.json 2>&1 || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/bandit-*.*, reports/safety-*.json', allowEmptyArchive: true
                }
            }
        }

        stage('Run Selenium Tests') {
            steps {
                echo 'Running Selenium tests in headless mode...'
                sh '''
                    . ${VENV_PATH}/bin/activate

                    # Run pytest with JUnit XML and HTML reports
                    pytest tests/ \
                        --headless \
                        --junitxml=${REPORTS_DIR}/junit-report.xml \
                        --html=${REPORTS_DIR}/test-report.html \
                        --self-contained-html \
                        -v \
                        --tb=short \
                        || true
                '''
            }
            post {
                always {
                    // Publish JUnit test results
                    junit allowEmptyResults: true, testResults: 'reports/junit-report.xml'

                    // Publish HTML test report
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'test-report.html',
                        reportName: 'Pytest HTML Report',
                        reportTitles: 'Test Results'
                    ])
                }
            }
        }

        stage('Quality Gate: Test Results Analysis') {
            steps {
                script {
                    echo 'Analyzing test results...'

                    def testResults = currentBuild.rawBuild.getAction(hudson.tasks.junit.TestResultAction.class)

                    if (testResults != null) {
                        def total = testResults.getTotalCount()
                        def failed = testResults.getFailCount()
                        def skipped = testResults.getSkipCount()
                        def passed = total - failed - skipped

                        if (total > 0) {
                            def passRate = (passed / total) * 100
                            passRate = passRate.round(2)

                            echo "========================================"
                            echo "         TEST RESULTS SUMMARY           "
                            echo "========================================"
                            echo "Total Tests:  ${total}"
                            echo "Passed:       ${passed}"
                            echo "Failed:       ${failed}"
                            echo "Skipped:      ${skipped}"
                            echo "Pass Rate:    ${passRate}%"
                            echo "Threshold:    ${TEST_PASS_THRESHOLD}%"
                            echo "========================================"

                            if (passRate < TEST_PASS_THRESHOLD.toInteger()) {
                                error "QUALITY GATE FAILED: Test pass rate ${passRate}% is below the ${TEST_PASS_THRESHOLD}% threshold"
                            } else {
                                echo "QUALITY GATE PASSED: Test pass rate ${passRate}% meets the ${TEST_PASS_THRESHOLD}% threshold"
                            }
                        } else {
                            echo 'WARNING: No tests were executed'
                        }
                    } else {
                        echo 'WARNING: No test results found. Ensure tests are generating JUnit XML reports.'
                    }
                }
            }
        }

        stage('Archive Artifacts') {
            steps {
                echo 'Archiving test artifacts...'
                archiveArtifacts artifacts: '''
                    reports/**/*,
                    screenshots/**/*,
                    Logs/**/*
                ''', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace...'
            cleanWs(
                cleanWhenNotBuilt: false,
                deleteDirs: true,
                disableDeferredWipeout: true,
                notFailBuild: true,
                patterns: [
                    [pattern: 'venv/**', type: 'INCLUDE'],
                    [pattern: '__pycache__/**', type: 'INCLUDE'],
                    [pattern: '.pytest_cache/**', type: 'INCLUDE']
                ]
            )
        }

        success {
            echo '''
            ========================================
                    BUILD SUCCESSFUL
            ========================================
            All quality gates passed!
            '''
        }

        failure {
            echo '''
            ========================================
                    BUILD FAILED
            ========================================
            Check the console output and reports
            for details on what went wrong.
            '''
        }

        unstable {
            echo '''
            ========================================
                    BUILD UNSTABLE
            ========================================
            Some tests failed but the build completed.
            Review the test reports for details.
            '''
        }
    }
}
