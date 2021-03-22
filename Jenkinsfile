pipeline {
  // Jenkins configuration dependencies
  //   Credentials:
  //     lib-ssdr-jenkins
  //
  //   Global Tool Configuration:
  //     JDK 8u121
  //     Git
  //     Maven 3.3.9
  //
  // This configuration utilizes the following Jenkins plugins:
  //
  //   * Warnings Next Generation
  //   * Email Extension Plugin
  //
  // This configuration also expects the following environment variables
  // to be set (typically in /apps/ci/config/env:
  //
  // JENKINS_EMAIL_SUBJECT_PREFIX
  //     The Email subject prefix identifying the server.
  //     Typically "[Jenkins - <HOSTNAME>]" where <HOSTNAME>
  //     is the name of the server, i.e. "[Jenkins - cidev]"
  //
  // JENKINS_DEFAULT_EMAIL_RECIPIENTS
  //     A comma-separated list of email addresses that should
  //    be the default recipients of Jenkins emails.
  //
  // JENKINS_MONITOR_HIPPO_JOBS_EMAIL_RECIPIENTS
  //     A comma-separated list of email addresses that should
  //     be sent "job monitor" emails for Hippo jobs (i.e., an
  //     email for every Hippo build job, where successful or failed).
  
  agent any

  tools {
    maven 'Maven 3.3.9'
    jdk 'JDK 8u121'
  }
  
  environment {
    MAVEN_OPTS = "-Xms512m -Xmx1024m"
    
    MAVEN_SETTINGS_XML = "--settings /apps/ci/maven-repository/settings.xml"
    
    DEFAULT_RECIPIENTS = "${ \
      sh(returnStdout: true, \
         script: 'echo $JENKINS_DEFAULT_EMAIL_RECIPIENTS').trim() \
    }"
      
    EMAIL_SUBJECT_PREFIX = "${ \
      sh(returnStdout: true, script: 'echo $JENKINS_EMAIL_SUBJECT_PREFIX').trim() \
    }"
    
    EMAIL_SUBJECT = "$EMAIL_SUBJECT_PREFIX - " +
                    '$PROJECT_NAME - ' +
                    'GIT_BRANCH_PLACEHOLDER - ' +
                    '$BUILD_STATUS! - ' +
                    "Build # $BUILD_NUMBER"

    EMAIL_CONTENT =
        '''$PROJECT_NAME - GIT_BRANCH_PLACEHOLDER - $BUILD_STATUS! - Build # $BUILD_NUMBER:
           |
           |Check console output at $BUILD_URL to view the results.
           |
           |There are ${ANALYSIS_ISSUES_COUNT} static analysis issues in this build.'''.stripMargin()
  }

  stages {
    stage('Initialize') {
      steps {
        script {
          // Retrieve the actual Git branch being built for use in email.
          //
          // For pull requests, the actual Git branch will be in the
          // CHANGE_BRANCH environment variable.
          //
          // For actual branch builds, the CHANGE_BRANCH variable won't exist
          // (and an exception will be thrown) but the branch name will be
          // part of the PROJECT_NAME variable, so it is not needed.
          
          ACTUAL_GIT_BRANCH = ''
          
          try {
            ACTUAL_GIT_BRANCH = CHANGE_BRANCH + ' - '
          } catch (groovy.lang.MissingPropertyException mpe) {
            // Do nothing. A branch (as opposed to a pull request) is being
            // built
          }            

          // Replace the "GIT_BRANCH_PLACEHOLDER" in email variables
          EMAIL_SUBJECT = EMAIL_SUBJECT.replaceAll('GIT_BRANCH_PLACEHOLDER - ', ACTUAL_GIT_BRANCH )
          EMAIL_CONTENT = EMAIL_CONTENT.replaceAll('GIT_BRANCH_PLACEHOLDER - ', ACTUAL_GIT_BRANCH )
        }
      }
    }
    
    stage('Build') {
      steps {
        // Run the maven build
        sh "mvn --batch-mode --show-version ${MAVEN_SETTINGS_XML} clean package"        
      }
      post {
        // Collect JUnit reports
        always {
          junit 'target/surefire-reports/*.xml' 
        }
      }
    }
    
    stage ('Analysis') {
      steps {
        sh "mvn --batch-mode --show-version ${MAVEN_SETTINGS_XML} checkstyle:checkstyle"
        
        // Collect Checkstyle reports
        recordIssues(tools: [checkStyle(reportEncoding: 'UTF-8')], unstableTotalAll: 1)
      }
    }
    
//    stage('Integration Test') {
//      steps {
//        // Lock the HIPPO_SELENIUM_PORT resource to prevent multiple Tomcats
//        // from running Selenium tests at the same time (and cause port
//        // collisions).
//        lock(resource: "HIPPO_SELENIUM_PORT_${env.NODE_NAME}") {
//          // Run the integration tests
//          sh "mvn --batch-mode --show-version ${MAVEN_SETTINGS_XML} -DrunSeleniumTests=true verify"
//        }
//        
//        // Collect reports
//        junit '**/target/failsafe-reports/*.xml'
//      }
//    }
    stage('Create install artifacts') {      
      steps {
        sh "mvn --batch-mode --show-version ${MAVEN_SETTINGS_XML} install"
        
      }
    }
    stage('CleanWorkspace') {
      steps {
        cleanWs()
      }
    }
  }
  
  post {
    always {
      emailext to: "$DEFAULT_RECIPIENTS",
               subject: "$EMAIL_SUBJECT",
               body: "$EMAIL_CONTENT"
    } 
  }
}
