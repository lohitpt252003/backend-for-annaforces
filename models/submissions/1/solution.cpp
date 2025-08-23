#include <bits/stdc++.h>
using namespace std;
int main() {
    int n, target;
    cin >> n;
    vector<int> arr(n);
    for(int i=0; i<n; i++) cin >> arr[i];
    cin >> target;
    unordered_map<int,int> mp;
    for(int i=0; i<n; i++) {
        if(mp.count(target-arr[i])) {
            cout << mp[target-arr[i]] << " " << i << endl;
            return 0;
        }
        mp[arr[i]] = i;
    }
}
