from collections import Counter, defaultdict


class FindingsAnalyzer:
    def __init__(self, findings):
        self.findings = findings

    def total(self):
        return len(self.findings)

    def by_service(self):
        counts = Counter(
            finding["service"]
            for finding in self.findings
        )

        return dict(counts)

    def by_risk(self):
        counts = Counter(
            finding["risk"]
            for finding in self.findings
        )

        return dict(counts)

    def by_finding(self):
        counts = Counter(
            finding["finding"]
            for finding in self.findings
        )

        return dict(counts)

    def grouped_by_service(self):
        grouped = defaultdict(list)

        for finding in self.findings:
            grouped[finding["service"]].append(finding)

        return dict(grouped)

    def summary(self):
        return {
            "total": self.total(),
            "by_service": self.by_service(),
            "by_risk": self.by_risk(),
            "by_finding": self.by_finding()
        }