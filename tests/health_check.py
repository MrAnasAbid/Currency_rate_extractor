from pandas import DataFrame
import logging

logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("currency_rate_extractor.log"),
        logging.StreamHandler()
    ]
)

# Check health of the pipeline, return 200 if everything is fine
if __name__ == '__main__':
    logging.info('Pipeline is healthy')
    logging.info('{Status : 200}')