#!/bin/bash
# mainframe_operations.sh
# Set up environment
export PATH=$PATH:/usr/lpp/java/J8.0_64/bin
export JAVA_HOME=/usr/lpp/java/J8.0_64
export PATH=$PATH:/usr/lpp/zowe/cli/node/bin
# Check Java availability
java -version
# Set ZOWE_USERNAME
ZOWE_USERNAME="Z15007" # Replace with the actual username

# where I'm ?
pwd
# Change to the cobol-check directory
cd cobol-check
echo "Changed to $(pwd)"
ls -al
# cobol-check is a JAR file, not an executable script
# We'll call it via java -jar
echo "cobol-check JAR found in bin/ directory"
# Make script in scripts directory executable
cd scripts
chmod +x linux_gnucobol_run_tests
echo "Made linux_gnucobol_run_tests executable"
cd ..
# Function to run cobol-check and copy files
run_cobolcheck() {
program=$1
echo "Running cobol-check for $program"
# Run cobol-check, but don't exit if it fails
java -jar bin/cobol-check-0.2.19.jar -p $program
echo "cobol-check execution completed for $program (exceptions may have occurred)"
# Check if CC##99.CBL was created in testruns/, regardless of cobol-check exit status
if [ -f "testruns/CC##99.CBL" ]; then
  # Copy to the MVS dataset
  if cp testruns/CC##99.CBL "//'${ZOWE_USERNAME}.CBL($program)'"; then
    echo "Copied testruns/CC##99.CBL to ${ZOWE_USERNAME}.CBL($program)"
  else
    echo "Failed to copy testruns/CC##99.CBL to ${ZOWE_USERNAME}.CBL($program)"
  fi
else
  echo "CC##99.CBL not found in testruns/ for $program"
fi
# Copy the JCL file if it exists
if [ -f "${program}.JCL" ]; then
  if cp ${program}.JCL "//'${ZOWE_USERNAME}.JCL($program)'"; then
    echo "Copied ${program}.JCL to ${ZOWE_USERNAME}.JCL($program)"
  else
    echo "Failed to copy ${program}.JCL to ${ZOWE_USERNAME}.JCL($program)"
  fi
else
  echo "${program}.JCL not found"
fi
}
# Run for each program (only those that exist)
for program in NUMBERS ALPHA; do
  run_cobolcheck $program
done
echo "Mainframe operations completed"
