from git import Repo
import subprocess
import pandas as pd
from io import StringIO
import sunpy_meta


path_to_repo = sunpy_meta.repo_path
print(path_to_repo)
repo = Repo(path_to_repo)

all_commits = [c for c in repo.iter_commits()]

#all_commits = all_commits[::-1]

MAX_COMMITS = 1000
SKIP_COMMITS = 10

print(len(all_commits))
commit_list = all_commits[::100]


g = repo.git

g.checkout('master')

dates = []
loc = []
files = []
comments = []
blanks = []


def count_lines_of_code(repo_path, verbose=False):
    """Count the lines of code by looking only at .py files. This makes use of the ohcount library which
    must be installed."""

    cmd = 'cloc'
    out = subprocess.Popen(f"{cmd} {repo_path}", shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.read()

    str = StringIO(out)
    for line in str:
        if line.startswith('--------'):
            break
    data = pd.read_csv(str, skiprows=0, skipfooter=3, skip_blank_lines=True, sep=r"[ ]{5,}",
                       index_col='Language', comment='-', engine='python')

    return data


for i, c in enumerate(sorted(commit_list, key=lambda x:x.committed_date)):
    g.checkout(c)
    dates.append(str(c.committed_datetime))
    print(f'{c.committed_datetime} {c.message}')

    data = count_lines_of_code(path_to_repo, verbose=True)
    files.append(data.sum()['files'])
    loc.append(data.sum()['code'])
    comments.append(data.sum()['comment'])
    blanks.append(data.sum()['blank'])

    if i > MAX_COMMITS:
         break


g.checkout('master')

result = pd.DataFrame(index=dates, data={'code': loc, 'comment': comments, 'blank': blanks, 'files': files})

result.to_csv("sunpy_history.csv")