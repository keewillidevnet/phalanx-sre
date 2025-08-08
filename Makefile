.PHONY: demo merge analyze ui clean

demo: merge analyze ui

merge:
	python examples/sample_pcap_merger.py
	python -m phalanx_agents.stitch_unit artifacts/sample_hop1.pcap artifacts/sample_hop2.pcap

analyze:
	python -m phalanx_agents.intel_unit artifacts/merged.pcap

ui:
	streamlit run ui/app.py

clean:
	rm -f artifacts/merged.pcap artifacts/diagnosis.json artifacts/explanation.md artifacts/sample_hop*.pcap
