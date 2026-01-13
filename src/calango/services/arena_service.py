from datetime import datetime

from tinydb import Query

try:
    import tiktoken
except ImportError:
    tiktoken = None


class ArenaService:
    def __init__(self, engine, interaction_manager, persistence_adapter):
        """
        Dependency Injection for Battle logic.
        Persistence adapter is typically the rinha_db TinyDB instance.
        """
        self.engine = engine
        self.interaction_manager = interaction_manager
        self.persistence_adapter = persistence_adapter

    def calculate_usage(self, model_name, prompt_text, response_text):
        """Same token calculation logic as ChatService for consistency."""
        if tiktoken:
            try:
                encoding = tiktoken.encoding_for_model(model_name)
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")
            prompt_tokens = len(encoding.encode(prompt_text))
            completion_tokens = len(encoding.encode(response_text))
        else:
            prompt_tokens = len(prompt_text) // 4
            completion_tokens = len(response_text) // 4

        total_tokens = prompt_tokens + completion_tokens
        input_price_per_m = 0.15
        output_price_per_m = 0.60
        cost = (prompt_tokens * input_price_per_m / 1_000_000) + (completion_tokens * output_price_per_m / 1_000_000)

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost,
        }

    def run_battle_round(self, prompt, contenders, system_prompt, persona_name):
        """
        Logic to run a prompt against multiple models.
        Handles error detection for quotas and updates global interaction history.
        """
        results = []
        messages = [{"role": "user", "content": prompt}]
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for contender in contenders:
            full_response = ""
            stats_text = "⚠️ Indisponível"
            error_occurred = False

            try:
                gen = self.engine.run_chat(
                    provider_name=contender["provider"],
                    model_name=contender["model"],
                    messages=messages,
                    session_id="rinha-mode",
                    persona_name=persona_name,
                    is_new_session=False,
                )

                for chunk in gen:
                    chunk_str = str(chunk) if chunk is not None else ""
                    # Content Inspection for Leaked JSON/Quota Errors
                    chunk_lower = chunk_str.lower()
                    is_quota_error = (
                        ("error" in chunk_lower and "429" in chunk_lower)
                        or ("quota" in chunk_lower and "exceeded" in chunk_lower)
                        or ("resource_exhausted" in chunk_lower)
                    )

                    if is_quota_error:
                        raise Exception("Quota Exceeded (Detected in Stream)")

                    full_response += chunk_str

                # Finalize stats for this fighter
                usage_stats = self.calculate_usage(contender["model"], f"{system_prompt}\n{prompt}", full_response)
                stats_text = f"💰 ${usage_stats['cost_usd']:.5f} | ⚡ {usage_stats['total_tokens']} tok"

                # Silently update interaction history if record exists
                try:
                    Log = Query()
                    records = self.interaction_manager.history_table.search(
                        (Log.session_id == "rinha-mode") & (Log.model == contender["model"])
                    )
                    if records:
                        self.interaction_manager.history_table.update(
                            {
                                "usage": usage_stats,
                                "cost_usd": usage_stats["cost_usd"],
                                "total_tokens": usage_stats["total_tokens"],
                            },
                            doc_ids=[records[-1].doc_id],
                        )
                except Exception:
                    pass

            except Exception as e:
                error_occurred = True
                err_str = str(e).lower()
                if any(k in err_str for k in ["quota", "429", "rate limit", "resource_exhausted"]):
                    full_response = f"**Cota Excedida** ({contender['model']})\n\nO limite gratuito foi atingido."
                else:
                    full_response = f"**Erro**\n\n{str(e)}"

            results.append(
                {
                    "model": contender["model"],
                    "content": full_response,
                    "stats": stats_text if not error_occurred else "⚠️ Falha",
                    "time": now_str,
                    "persona": persona_name,
                }
            )

        return results

    def save_round(self, prompt, results):
        """Persists the battle round results to the rinha store."""
        new_round = {"prompt": prompt, "results": results}
        self.persistence_adapter.insert(new_round)
        return new_round
