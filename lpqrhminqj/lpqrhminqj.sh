mkdir instructlab
cd instructlab
python3 -m venv venv
source venv/bin/activate
pip install git+https://github.com/instructlab/instructlab.git@stable
ilab
git clone https://github.com/instructlab/taxonomy
ilab init
ilab download
ilab serve > output.log 2>&1 &
ilab chat