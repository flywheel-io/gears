FROM ubuntu:14.04

ENV GEAR_BASE_DIR=/flywheel/v0

ENV GEAR_INPUT_DIR="${GEAR_BASE_DIR}/input" \
  GEAR_OUTPUT_DIR="${GEAR_BASE_DIR}/output" \
  GEAR_INFO_FILE="${GEAR_BASE_DIR}/info.toml" \
  GEAR_ENTRYPOINT="${GEAR_BASE_DIR}/run"


RUN mkdir -p "${GEAR_INPUT_DIR}" \
  && mkdir -p "${GEAR_OUTPUT_DIR}" \


COPY info.toml "${GEAR_INFO_FILE}"
COPY entrypoint.sh "${GEAR_ENTRYPOINT}"


WORKDIR ${GEAR_BASE_DIR}
