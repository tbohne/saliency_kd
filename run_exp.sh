for i in {1..20}; do
    python saliency_kd/llm_analysis.py --mode ts --input llm_input/Mallat/class_0/centroids4llm.npy --model o3-2025-04-16 >> output.txt
done
