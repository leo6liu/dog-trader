package main

import (
	"context"
	"fmt"
	"os"

	"strings"

	openai "github.com/sashabaranov/go-openai"
)

func main() {
    tickers := []string{"AAPL", "TSLA"}

    client := openai.NewClient(os.Getenv("OPENAI_API_KEY"))
    body := fmt.Sprintf("What does TipRanks think about %s today?", strings.Join(tickers, ", "))
    fmt.Println(body)
       
    resp, err := client.CreateChatCompletion(
        context.Background(),
        openai.ChatCompletionRequest{
            Model: openai.GPT3Dot5Turbo,
            Messages: []openai.ChatCompletionMessage{
                {
                    Role: openai.ChatMessageRoleUser,
                    Content: body,
                },
            },
        },
    )

    if err != nil {
        fmt.Printf("ChatCompletion error: %v\n", err)
        return
    }

    fmt.Println(resp.Choices[0].Message.Content)
}