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
    body := fmt.Sprintf("Rate each of %s media attention this week from 0 to 9, with 0 being terrible and 9 being extremely positive", strings.Join(tickers, ", "))
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