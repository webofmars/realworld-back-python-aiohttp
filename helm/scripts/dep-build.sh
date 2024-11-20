#!/bin/sh

set -eu

if [ -z "$1" ]; then
  echo "Usage: $0 <helm chart dir>"
  exit 1
fi

HELM_CHART_DIR="$(realpath "$1")"

if [ ! -d "${HELM_CHART_DIR}" ]; then
  echo "Error: helm chart dir '${HELM_CHART_DIR}' does not exist"
  exit 1
fi

# Function to find and process Chart.yaml files
process_chart_files() {
  _chart_dir="$1"
  _mode="$2"
  _temp_file="$3"

  find "${_chart_dir}" -name Chart.yaml -mindepth 1 -exec dirname {} \; | while read -r subchart_dir; do
    case "${_mode}" in
      "gathering")
        echo "+ gathering dependencies for $subchart_dir"
        (
          cd "$subchart_dir" &&
          yq eval '.dependencies[].repository' Chart.yaml |
          grep -E '^(https?|git)://' |
          while read -r repo; do
            if ! grep -q "$repo" "${_temp_file}"; then
              echo "$repo" >> "${_temp_file}"
            else
              echo "+ skipping duplicate repository $repo"
            fi
          done
        )
        ;;
      "building")
        echo "+ building dependencies for $subchart_dir"
        (cd "$subchart_dir" && helm dependency build --skip-refresh .)
        ;;
      *)
        echo "Error: Unknown mode '${_mode}'"
        exit 1
        ;;
    esac
  done
}

echo "+ building helm dependencies for subcharts"
INITIAL_DIR="$(pwd)"

# Create a temporary file for unique repositories
unique_repos_file=$(mktemp)

# Process subchart dependencies (gather repositories)
process_chart_files "${HELM_CHART_DIR}" "gathering" "${unique_repos_file}"

# Add all unique repositories
while IFS= read -r repo; do
  repo_name="$(echo "${repo}" | md5sum | cut -d' ' -f1)"
  echo "+ adding helm repo ${repo} as ${repo_name}"
  (helm repo add "${repo_name}" "${repo}" && helm repo update "${repo_name}")
done < "${unique_repos_file}"

# Process subchart dependencies again (build dependencies)
process_chart_files "${HELM_CHART_DIR}" "building" "${unique_repos_file}"

cd "${INITIAL_DIR}" || exit 1

# Clean up temporary file
rm -f "${unique_repos_file}"

echo "+ exiting successfully"
exit 0
